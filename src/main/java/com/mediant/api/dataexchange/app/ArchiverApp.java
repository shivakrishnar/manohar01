package com.mediant.api.dataexchange.app;

import com.mediant.api.dataexchange.dao.ClientDao;
import com.mediant.api.dataexchange.dao.CredentialDao;
import com.mediant.api.dataexchange.http.TriggerFetcher;
import com.mediant.api.dataexchange.security.TokenProvider;
import com.mediant.api.dataexchange.storage.LocalUploader;
import com.mediant.api.dataexchange.storage.S3Uploader;
import com.mediant.api.dataexchange.storage.StorageUploader;
import com.mediant.api.dataexchange.service.ArchiverService;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

import javax.sql.DataSource;
import java.io.FileInputStream;
import java.util.Properties;

public class ArchiverApp {
    public static void main(String[] args) throws Exception {
        Properties p = new Properties();
        String propsFile = args.length > 0 ? args[0] : "src/main/resources/application.properties";
        try (FileInputStream fis = new FileInputStream(propsFile)) {
            p.load(fis);
        }

        // Setup DataSource
        HikariConfig cfg = new HikariConfig();
        cfg.setJdbcUrl(p.getProperty("db.url"));
        cfg.setUsername(p.getProperty("db.user"));
        cfg.setPassword(p.getProperty("db.password"));
        DataSource ds = new HikariDataSource(cfg);

        String clientsQuery = p.getProperty("db.clients.query");
        ClientDao clientDao = new ClientDao(ds, clientsQuery);
        CredentialDao credentialDao = new CredentialDao(ds);

        TriggerFetcher fetcher = new TriggerFetcher(p.getProperty("dex.base.url"));
        TokenProvider tokenProvider = new TokenProvider(credentialDao, p.getProperty("oauth.token.url"));

        StorageUploader uploader;
        String storageMode = p.getProperty("storage.mode", "local");
        if ("s3".equalsIgnoreCase(storageMode)) {
            uploader = new S3Uploader(p.getProperty("s3.region"), p.getProperty("s3.bucket"));
        } else {
            uploader = new LocalUploader(p.getProperty("local.output.dir", "./archive-output"));
        }

        ArchiverService svc = new ArchiverService(clientDao, fetcher, uploader, tokenProvider, p.getProperty("file.date.format", "yyyyMMdd"));
        svc.runArchive();

        System.out.println("Archive run completed");
    }
}
