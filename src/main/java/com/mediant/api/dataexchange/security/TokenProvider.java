package com.mediant.api.dataexchange.security;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.mediant.api.dataexchange.dao.CredentialDao;
import com.mediant.api.dataexchange.model.ClientCredential;
import org.apache.hc.client5.http.classic.methods.HttpPost;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.client5.http.entity.UrlEncodedFormEntity;
import org.apache.hc.core5.http.NameValuePair;
import org.apache.hc.core5.http.message.BasicNameValuePair;

import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class TokenProvider {
    private final CredentialDao credDao;
    private final ObjectMapper mapper = new ObjectMapper();

    public TokenProvider(CredentialDao credDao, String tokenUrlTemplate) {
        this.credDao = credDao;
    }

    public Optional<String> getTokenForCredentialId(Long credId) throws Exception {
        if (credId == null) return Optional.empty();
        Optional<ClientCredential> maybe = credDao.findById(credId);
        if (maybe.isEmpty()) return Optional.empty();
        ClientCredential cred = maybe.get();

        try (CloseableHttpClient client = HttpClients.createDefault()) {
            HttpPost post = new HttpPost(cred.getTokenUrl());
            List<NameValuePair> params = new ArrayList<>();
            params.add(new BasicNameValuePair("grant_type", "client_credentials"));
            params.add(new BasicNameValuePair("client_id", cred.getClientId()));
            params.add(new BasicNameValuePair("client_secret", cred.getClientSecret()));
            post.setEntity(new UrlEncodedFormEntity(params, StandardCharsets.UTF_8));

            return client.execute(post, resp -> {
                int sc = resp.getCode();
                if (sc >= 200 && sc < 300) {
                    try (InputStream is = resp.getEntity().getContent()) {
                        JsonNode node = mapper.readTree(is);
                        if (node.has("access_token")) {
                            return Optional.of(node.get("access_token").asText());
                        }
                        return Optional.empty();
                    }
                }
                return Optional.empty();
            });
        }
    }
}
