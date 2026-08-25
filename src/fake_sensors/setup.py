from setuptools import find_packages, setup

package_name = 'fake_sensors'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='greyman-ubuntu',
    maintainer_email='70279710+asaisriram@users.noreply.github.com',
    description='Package for simulation of fake sensors',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [ 'counter_publisher = fake_sensors.counter_publisher:main',
        ],
    },
)
