from setuptools import setup, find_packages

setup(
    name="animation-tools-common",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PySide6>=6.0.0",
    ],
    author="あなたの名前",
    description="アニメーション制作ツール用の共通コンポーネント",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/animtools/animation-tools-common",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
