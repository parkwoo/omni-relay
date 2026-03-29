from setuptools import setup, find_packages

setup(
    name="omnirelay",
    version="1.4.0",
    description="OmniRelay for OpenClaw - The resilient AI dispatching layer. One API, zero downtime.",
    author="parkwoo",
    url="https://github.com/parkwoo/omni-relay",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
        "google-genai>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "relay=omnirelay.cli:main",
        ],
    },
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
