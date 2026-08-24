import pytest

def calculate_house_whole_sign(planet_sign, lagna_sign):
    return ((planet_sign - lagna_sign) % 12) + 1

def test_whole_sign_categorical_matrix():
    for lagna in range(12):
        for planet in range(12):
            house = calculate_house_whole_sign(planet, lagna)
            assert 1 <= house <= 12
            if planet == lagna: assert house == 1
            if planet == (lagna + 6) % 12: assert house == 7
