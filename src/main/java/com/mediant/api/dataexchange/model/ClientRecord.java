package com.mediant.api.dataexchange.model;

public class ClientRecord {
    private final long clientId;
    private final String name;
    private final Long oauth2CredentialsId; // nullable

    public ClientRecord(long clientId, String name, Long oauth2CredentialsId) {
        this.clientId = clientId;
        this.name = name;
        this.oauth2CredentialsId = oauth2CredentialsId;
    }

    public long getClientId() { return clientId; }
    public String getName() { return name; }
    public Long getOauth2CredentialsId() { return oauth2CredentialsId; }
}
