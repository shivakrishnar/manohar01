package com.mediant.api.dataexchange.http;

import org.apache.hc.client5.http.classic.methods.HttpGet;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;

import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Scanner;

public class TriggerFetcher {
    private final String baseUrl;

    public TriggerFetcher(String baseUrl) {
        this.baseUrl = baseUrl;
    }

    public String fetch(long clientId, String bearerToken) throws Exception {
        String url = baseUrl + "/data-exchange/trigger?clientId=" + clientId;
        try (CloseableHttpClient client = HttpClients.createDefault()) {
            HttpGet get = new HttpGet(url);
            if (bearerToken != null && !bearerToken.isEmpty()) {
                get.setHeader("Authorization", "Bearer " + bearerToken);
            }
            return client.execute(get, resp -> {
                int sc = resp.getCode();
                if (sc >= 200 && sc < 300) {
                    try (InputStream is = resp.getEntity().getContent();
                         Scanner s = new Scanner(is, StandardCharsets.UTF_8.name())) {
                        s.useDelimiter("\\A");
                        return s.hasNext() ? s.next() : "";
                    }
                }
                throw new IllegalStateException("trigger fetch failed: " + sc);
            });
        }
    }
}
