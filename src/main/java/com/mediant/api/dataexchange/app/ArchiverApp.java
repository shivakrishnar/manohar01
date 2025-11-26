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
        DataSource ds;
        try {
            ds = new HikariDataSource(cfg);
        } catch (Exception e) {
            System.err.println("Failed to initialize database connection to '" + p.getProperty("db.url") + "'.");
            System.err.println("Reason: " + e.getMessage());
            System.err.println("Make sure the database is reachable and the JDBC properties are correct in " + propsFile + ".");
            System.err.println("If you don't want to connect to a real database during development, set a valid 'db.*' URL or run the app in a test mode.");
            // Exit explicitly to avoid an uncaught stacktrace from Hikari
            System.exit(1);
            return;
        }

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
