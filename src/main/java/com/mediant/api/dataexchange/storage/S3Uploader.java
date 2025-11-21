package com.mediant.api.dataexchange.storage;

import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

public class S3Uploader implements StorageUploader {
    private final S3Client s3;
    private final String bucket;

    public S3Uploader(String region, String bucket) {
        this.bucket = bucket;
        this.s3 = S3Client.builder().region(Region.of(region)).build();
    }

    @Override
    public void upload(String key, String content) throws Exception {
        PutObjectRequest req = PutObjectRequest.builder()
                .bucket(bucket)
                .key(key)
                .build();
        s3.putObject(req, RequestBody.fromString(content));
    }
}
