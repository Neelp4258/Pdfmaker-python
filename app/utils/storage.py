"""Storage backend for generated PDFs (local, S3, GCS)."""
import os
import time
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageBackend:
    """Abstract storage backend for PDF files."""

    def __init__(self, config):
        """Initialize storage backend based on configuration."""
        self.config = config
        self.storage_type = config.STORAGE_TYPE.lower()

        if self.storage_type == 'local':
            self.storage_path = Path(config.STORAGE_PATH)
            self.storage_path.mkdir(parents=True, exist_ok=True)

    def save_pdf(self, job_id: str, pdf_bytes: bytes) -> str:
        """
        Save PDF file to storage.

        Args:
            job_id: Unique job identifier
            pdf_bytes: PDF content as bytes

        Returns:
            File path or storage key
        """
        if self.storage_type == 'local':
            return self._save_local(job_id, pdf_bytes)
        elif self.storage_type == 's3':
            return self._save_s3(job_id, pdf_bytes)
        elif self.storage_type == 'gcs':
            return self._save_gcs(job_id, pdf_bytes)
        else:
            raise ValueError(f"Unknown storage type: {self.storage_type}")

    def _save_local(self, job_id: str, pdf_bytes: bytes) -> str:
        """Save PDF to local filesystem."""
        file_path = self.storage_path / f"{job_id}.pdf"
        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f"Saved PDF to local storage: {file_path}")
        return str(file_path)

    def _save_s3(self, job_id: str, pdf_bytes: bytes) -> str:
        """Save PDF to AWS S3."""
        try:
            import boto3
            s3 = boto3.client('s3', region_name=self.config.S3_REGION)
            key = f"pdfs/{job_id}.pdf"
            s3.put_object(
                Bucket=self.config.S3_BUCKET,
                Key=key,
                Body=pdf_bytes,
                ContentType='application/pdf',
                ServerSideEncryption='AES256'
            )
            logger.info(f"Saved PDF to S3: s3://{self.config.S3_BUCKET}/{key}")
            return key
        except ImportError:
            raise RuntimeError("boto3 not installed. Install with: pip install boto3")

    def _save_gcs(self, job_id: str, pdf_bytes: bytes) -> str:
        """Save PDF to Google Cloud Storage."""
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(self.config.GCS_BUCKET)
            blob = bucket.blob(f"pdfs/{job_id}.pdf")
            blob.upload_from_string(pdf_bytes, content_type='application/pdf')
            logger.info(f"Saved PDF to GCS: gs://{self.config.GCS_BUCKET}/{blob.name}")
            return blob.name
        except ImportError:
            raise RuntimeError("google-cloud-storage not installed. Install with: pip install google-cloud-storage")

    def get_download_url(self, job_id: str) -> str:
        """
        Get download URL for PDF.

        Args:
            job_id: Unique job identifier

        Returns:
            Download URL
        """
        if self.storage_type == 'local':
            return f"/download/{job_id}"
        elif self.storage_type == 's3':
            return self._get_s3_url(job_id)
        elif self.storage_type == 'gcs':
            return self._get_gcs_url(job_id)
        else:
            raise ValueError(f"Unknown storage type: {self.storage_type}")

    def _get_s3_url(self, job_id: str) -> str:
        """Generate S3 presigned URL."""
        try:
            import boto3
            s3 = boto3.client('s3', region_name=self.config.S3_REGION)
            key = f"pdfs/{job_id}.pdf"
            url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.config.S3_BUCKET, 'Key': key},
                ExpiresIn=3600  # 1 hour
            )
            return url
        except ImportError:
            raise RuntimeError("boto3 not installed")

    def _get_gcs_url(self, job_id: str) -> str:
        """Generate GCS signed URL."""
        try:
            from google.cloud import storage
            from datetime import timedelta
            client = storage.Client()
            bucket = client.bucket(self.config.GCS_BUCKET)
            blob = bucket.blob(f"pdfs/{job_id}.pdf")
            url = blob.generate_signed_url(expiration=timedelta(hours=1))
            return url
        except ImportError:
            raise RuntimeError("google-cloud-storage not installed")

    def get_pdf(self, job_id: str) -> Optional[bytes]:
        """
        Retrieve PDF from storage.

        Args:
            job_id: Unique job identifier

        Returns:
            PDF bytes or None if not found
        """
        if self.storage_type == 'local':
            file_path = self.storage_path / f"{job_id}.pdf"
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    return f.read()
            return None
        elif self.storage_type == 's3':
            return self._get_s3_pdf(job_id)
        elif self.storage_type == 'gcs':
            return self._get_gcs_pdf(job_id)
        else:
            raise ValueError(f"Unknown storage type: {self.storage_type}")

    def _get_s3_pdf(self, job_id: str) -> Optional[bytes]:
        """Get PDF from S3."""
        try:
            import boto3
            s3 = boto3.client('s3', region_name=self.config.S3_REGION)
            key = f"pdfs/{job_id}.pdf"
            response = s3.get_object(Bucket=self.config.S3_BUCKET, Key=key)
            return response['Body'].read()
        except Exception as e:
            logger.warning(f"Failed to retrieve PDF from S3: {e}")
            return None

    def _get_gcs_pdf(self, job_id: str) -> Optional[bytes]:
        """Get PDF from GCS."""
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(self.config.GCS_BUCKET)
            blob = bucket.blob(f"pdfs/{job_id}.pdf")
            return blob.download_as_bytes()
        except Exception as e:
            logger.warning(f"Failed to retrieve PDF from GCS: {e}")
            return None

    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old PDF files.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of files deleted
        """
        if self.storage_type != 'local':
            logger.warning(f"Cleanup not implemented for {self.storage_type}")
            return 0

        deleted_count = 0
        cutoff_time = time.time() - (max_age_hours * 3600)

        for file_path in self.storage_path.glob("*.pdf"):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                deleted_count += 1
                logger.debug(f"Deleted old PDF: {file_path}")

        return deleted_count
