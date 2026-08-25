from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'my_py_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (
            os.path.join("share", package_name, "javino_config"),
            glob("javino_config/*.yaml"),
        ),
    ],
    install_requires=[
        "setuptools",
        "PyYAML",
        "pyserial",
    ],
    zip_safe=True,
    maintainer='labra2',
    maintainer_email='labra2@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "blinker_publisher = my_py_pkg.blinker_publisher:main",
            "blinker_subscriber = my_py_pkg.blinker_subscriber:main",
            "blinker_bridge = my_py_pkg.blinker_bridge:main",
            "javino_ros_bridge = my_py_pkg.javino_ros_bridge:main",
            "blinker_on_off = my_py_pkg.blinker_on_off:main",
        ],
    },
)
