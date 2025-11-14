"""
Pytest configuration and shared fixtures
"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import shutil
import numpy as np
import cv2

# Python source path'i ekle
sys.path.insert(0, str(Path(__file__).parent.parent / 'python_src'))


@pytest.fixture(scope='session')
def test_images_dir():
    """Test görüntüleri için geçici dizin"""
    return Path(__file__).parent / 'fixtures' / 'test_images'


@pytest.fixture
def temp_db():
    """Geçici test veritabanı"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    yield path

    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def sample_image(test_images_dir):
    """Örnek test görüntüsü oluştur"""
    os.makedirs(test_images_dir, exist_ok=True)

    image_path = test_images_dir / 'test_vehicle.jpg'

    # 600x450 boyutunda örnek görüntü oluştur
    img = np.random.randint(0, 255, (450, 600, 3), dtype=np.uint8)

    # Beyaz bir bölge ekle (renk tespiti için)
    img[100:250, 100:350] = [220, 220, 220]  # BGR - Beyaz
    img[100:250, 350:600] = [220, 220, 220]  # BGR - Beyaz

    cv2.imwrite(str(image_path), img)

    yield str(image_path)

    # Cleanup gerekirse
    # image_path.unlink(missing_ok=True)


@pytest.fixture
def white_car_image(test_images_dir):
    """Beyaz araç görüntüsü"""
    os.makedirs(test_images_dir, exist_ok=True)

    image_path = test_images_dir / 'white_car.jpg'

    img = np.zeros((450, 600, 3), dtype=np.uint8)
    # Beyaz renk (BGR)
    img[100:250, 100:350] = [240, 240, 235]
    img[100:250, 350:600] = [235, 240, 240]

    cv2.imwrite(str(image_path), img)

    return str(image_path)


@pytest.fixture
def black_car_image(test_images_dir):
    """Siyah araç görüntüsü"""
    os.makedirs(test_images_dir, exist_ok=True)

    image_path = test_images_dir / 'black_car.jpg'

    img = np.zeros((450, 600, 3), dtype=np.uint8)
    # Siyah renk (BGR)
    img[100:250, 100:350] = [50, 50, 50]
    img[100:250, 350:600] = [60, 55, 50]

    cv2.imwrite(str(image_path), img)

    return str(image_path)


@pytest.fixture
def red_car_image(test_images_dir):
    """Kırmızı araç görüntüsü"""
    os.makedirs(test_images_dir, exist_ok=True)

    image_path = test_images_dir / 'red_car.jpg'

    img = np.zeros((450, 600, 3), dtype=np.uint8)
    # Kırmızı renk (BGR)
    img[100:250, 100:350] = [50, 50, 180]
    img[100:250, 350:600] = [60, 60, 190]

    cv2.imwrite(str(image_path), img)

    return str(image_path)
