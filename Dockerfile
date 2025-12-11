FROM python:3.12-slim

LABEL org.opencontainers.image.source=https://github.com/tedg-dev/merge_spdx_sboms
LABEL org.opencontainers.image.description="SPDX SBOM Merger Tool"
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY setup.py .
COPY README.md .

RUN pip install --no-cache-dir -e .

RUN useradd -m -u 1000 sbomuser && \
    chown -R sbomuser:sbomuser /app

USER sbomuser

ENTRYPOINT ["python", "-m", "sbom_merger.cli"]
CMD ["--help"]
