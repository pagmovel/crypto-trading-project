from setuptools import setup, find_packages

setup(
    name="options-center",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "ccxt>=4.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "plotly>=5.3.0",
        "python-dotenv>=0.19.0",
        "pytest>=6.2.5",
        "aiohttp>=3.8.0",
        "python-dateutil>=2.8.2",
        "dash>=2.0.0",
        "dash-bootstrap-components>=1.0.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "websockets>=10.0",
        "black>=22.0.0",  # Para formatação de código
        "mypy>=0.910",    # Para checagem de tipos
        "pytest-asyncio>=0.15.0",  # Para testes assíncronos
        "pytest-cov>=2.12.0",      # Para cobertura de testes
    ],
    python_requires=">=3.9",
    author="Options Center Team",
    author_email="contact@optionscenter.com",
    description="Uma plataforma para análise e trading de opções de criptomoedas",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/options-center/crypto-trading-project",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
)