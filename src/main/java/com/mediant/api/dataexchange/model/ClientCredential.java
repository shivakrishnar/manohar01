package com.mediant.api.dataexchange.model;

public class ClientCredential {
    private final long id;
    private final String clientId;
    private final String clientSecret;
    private final String tokenUrl;

    public ClientCredential(long id, String clientId, String clientSecret, String tokenUrl) {
        this.id = id;
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.tokenUrl = tokenUrl;
    }

    public long getId() { return id; }
    public String getClientId() { return clientId; }
    public String getClientSecret() { return clientSecret; }
    public String getTokenUrl() { return tokenUrl; }
}
