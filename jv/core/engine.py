import swisseph as swe
import threading
import hashlib
import json
import pathlib
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_se_lock = threading.Lock()
CALC_VERSION = "JV-CALC-1.3"

_MANIFEST_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / "ephemeris_provenance_manifest.json"
if _MANIFEST_PATH.exists():
    _MANIFEST = json.loads(_MANIFEST_PATH.read_text())
    EPHEMERIS_DATA_HASH = _MANIFEST.get("ephemeris_data_hash", "PENDING_MANIFEST_GENERATION")
else:
    EPHEMERIS_DATA_HASH = "PENDING_MANIFEST_GENERATION"

def angular_diff(a, b):
    return abs((a - b + 180) % 360 - 180)

def compute(y, mo, d, h, mi, tz_name, lat, lon, ayan="lahiri", node="true", house="whole"):
    with _se_lock:
        sid_modes = {"lahiri": swe.SIDM_LAHIRI, "raman": swe.SIDM_RAMAN, "kp": swe.SIDM_KRISHNAMURTI}
        if ayan not in sid_modes:
            raise ValueError("Unsupported ayanamsha")
        swe.set_sid_mode(sid_modes[ayan])

        try:
            tz = ZoneInfo(tz_name)
            local_dt = datetime(y, mo, d, h, mi, tzinfo=tz)
            utc_dt = local_dt.astimezone(timezone.utc)

            round_trip = utc_dt.astimezone(tz)
            if round_trip.replace(tzinfo=None) != local_dt.replace(tzinfo=None):
                raise ValueError(f"Nonexistent local time: {y}-{mo}-{d} {h}:{mi} in {tz_name}.")

            dt_fold0 = datetime(y, mo, d, h, mi, tzinfo=tz, fold=0)
            dt_fold1 = datetime(y, mo, d, h, mi, tzinfo=tz, fold=1)
            if dt_fold0.astimezone(timezone.utc) != dt_fold1.astimezone(timezone.utc):
                raise ValueError(f"Ambiguous local time: {y}-{mo}-{d} {h}:{mi} in {tz_name}.")

        except ZoneInfoNotFoundError:
            raise ValueError(f"Timezone {tz_name} not found in IANA database.")

        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                        utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600)

        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        planets = {}
        bodies = {"su": swe.SUN, "mo": swe.MOON, "ma": swe.MARS, "me": swe.MERCURY,
                  "jp": swe.JUPITER, "ve": swe.VENUS, "sa": swe.SATURN}

        for pid, body in bodies.items():
            res, _ = swe.calc_ut(jd, body, flags)
            lon_sid = res[0]
            planets[pid] = {
                "lon": lon_sid, "sign": int(lon_sid // 30),
                "nak": int(lon_sid // (360/27)), "pada": int((lon_sid % (360/27)) // (360/108)) + 1,
                "retro": res[3] < 0, "motion_source": "calculated"
            }

        node_body = swe.TRUE_NODE if node == "true" else swe.MEAN_NODE
        res, _ = swe.calc_ut(jd, node_body, flags)
        ra_lon = res[0]
        planets["ra"] = {"lon": ra_lon, "sign": int(ra_lon // 30), "nak": int(ra_lon // (360/27)),
                         "pada": int((ra_lon % (360/27)) // (360/108)) + 1, "retro": True, "motion_source": "astrological_convention"}
        ke_lon = (ra_lon + 180) % 360
        planets["ke"] = {"lon": ke_lon, "sign": int(ke_lon // 30), "nak": int(ke_lon // (360/27)),
                         "pada": int((ke_lon % (360/27)) // (360/108)) + 1, "retro": True, "motion_source": "astrological_convention"}

        house_flags = swe.FLG_SIDEREAL
        cusps, asmc = swe.houses_ex(jd, house_flags, lat, lon, b"P")
        lagna_sid = asmc[0]
        lagna_sign = int(lagna_sid // 30)

        if house != "whole":
            raise NotImplementedError(f"House system '{house}' is NOT CERTIFIED.")
        houses = {pid: ((p["sign"] - lagna_sign) % 12) + 1 for pid, p in planets.items()}

        config = {"zodiac": "sidereal", "ayanamsha": ayan, "node": node, "house": house, "coordinate": "geocentric"}
        versions = {"engine": f"SwissEph {swe.version}", "calc": CALC_VERSION, "ephemeris_data_hash": EPHEMERIS_DATA_HASH}

        payload = json.dumps({
            "i": {"y": y, "mo": mo, "d": d, "h": h, "mi": mi, "tz": tz_name, "lat": lat, "lon": lon},
            "c": config, "o": {"planets": planets, "houses": houses, "lagna_sign": lagna_sign, "lagna_sid": lagna_sid},
            "v": versions
        }, sort_keys=True, separators=(',', ':'))

        return {
            "fingerprint": hashlib.sha256(payload.encode('utf-8')).hexdigest(),
            "lagna_sid": lagna_sid, "lagna_sign": lagna_sign,
            "planets": planets, "houses": houses, "utc": utc_dt.isoformat(),
            "config": config, "versions": versions
        }