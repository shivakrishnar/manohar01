package com.mediant.api.dataexchange.storage;

public interface StorageUploader {
    void upload(String key, String content) throws Exception;
}
