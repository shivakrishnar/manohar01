package com.mediant.api.dataexchange.service;

import com.mediant.api.dataexchange.dao.ClientDao;
import com.mediant.api.dataexchange.http.TriggerFetcher;
import com.mediant.api.dataexchange.model.ClientRecord;
import com.mediant.api.dataexchange.security.TokenProvider;
import com.mediant.api.dataexchange.storage.StorageUploader;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;

public class ArchiverService {
    private final ClientDao clientDao;
    private final TriggerFetcher fetcher;
    private final StorageUploader uploader;
    private final TokenProvider tokenProvider;
    private final DateTimeFormatter dateFmt;

    public ArchiverService(ClientDao clientDao, TriggerFetcher fetcher, StorageUploader uploader, TokenProvider tokenProvider, String dateFormat) {
        this.clientDao = clientDao;
        this.fetcher = fetcher;
        this.uploader = uploader;
        this.tokenProvider = tokenProvider;
        this.dateFmt = DateTimeFormatter.ofPattern(dateFormat);
    }

    public void runArchive() throws Exception {
        List<ClientRecord> clients = clientDao.listClientsToArchive();
        String date = LocalDate.now().format(dateFmt);
        for (ClientRecord c : clients) {
            String token = null;
            if (c.getOauth2CredentialsId() != null && tokenProvider != null) {
                token = tokenProvider.getTokenForCredentialId(c.getOauth2CredentialsId()).orElse(null);
            }

            String resp = fetcher.fetch(c.getClientId(), token);
            String key = String.format("trigger/%d/file/%d_trigger_%s.json", c.getClientId(), c.getClientId(), date);
            uploader.upload(key, resp);
        }
    }
}
