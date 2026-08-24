import pytest
from jv.core.engine import compute

def test_true_vs_mean_node():
    base_kwargs = dict(y=1990, mo=8, d=15, h=6, mi=0, tz_name="Asia/Kolkata", lat=25.3, lon=82.9, ayan="lahiri")
    true_node_chart = compute(node="true", **base_kwargs)
    mean_node_chart = compute(node="mean", **base_kwargs)
    
    # True and Mean nodes are almost never in the exact same degree
    assert true_node_chart['planets']['ra']['lon'] != mean_node_chart['planets']['ra']['lon']
    
    # Both must be marked as astrological convention retrograde
    assert true_node_chart['planets']['ra']['motion_source'] == "astrological_convention"
    assert mean_node_chart['planets']['ra']['motion_source'] == "astrological_convention"
