package com.mediant.api.dataexchange.dao;

import com.mediant.api.dataexchange.model.ClientCredential;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Optional;

public class CredentialDao {
    private final DataSource ds;

    public CredentialDao(DataSource ds) {
        this.ds = ds;
    }

    /**
     * Fetch credential by ID. Assumes table `OAuth2ClientCredentials` with columns
     * `ClientCredentialsID` (PK), `ClientId`, `ClientSecret`, `TokenUrl`.
     */
    public Optional<ClientCredential> findById(long id) throws Exception {
        try (Connection c = ds.getConnection();
             PreparedStatement ps = c.prepareStatement("SELECT ClientId, ClientSecret, TokenUrl FROM OAuth2ClientCredentials WHERE ClientCredentialsID = ?")) {
            ps.setLong(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    String clientId = rs.getString(1);
                    String clientSecret = rs.getString(2);
                    String tokenUrl = rs.getString(3);
                    return Optional.of(new ClientCredential(id, clientId, clientSecret, tokenUrl));
                }
            }
        }
        return Optional.empty();
    }
}
