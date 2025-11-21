package com.mediant.api.dataexchange.storage;

import java.io.File;
import java.io.FileWriter;

public class LocalUploader implements StorageUploader {
    private final File baseDir;

    public LocalUploader(String basePath) {
        this.baseDir = new File(basePath);
        if (!baseDir.exists()) baseDir.mkdirs();
    }

    @Override
    public void upload(String key, String content) throws Exception {
        File out = new File(baseDir, key);
        File parent = out.getParentFile();
        if (parent != null && !parent.exists()) parent.mkdirs();
        try (FileWriter fw = new FileWriter(out)) {
            fw.write(content);
        }
    }
}
