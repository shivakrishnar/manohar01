package com.mediant.api.dataexchange.dao;

import com.mediant.api.dataexchange.model.ClientRecord;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

public class ClientDao {
    private final DataSource ds;
    private final String clientsQuery;

    public ClientDao(DataSource ds, String clientsQuery) {
        this.ds = ds;
        this.clientsQuery = clientsQuery;
    }

    public List<ClientRecord> listClientsToArchive() throws Exception {
        List<ClientRecord> result = new ArrayList<>();
        try (Connection c = ds.getConnection();
             PreparedStatement ps = c.prepareStatement(clientsQuery)) {
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    long id = rs.getLong(1);
                    String name = rs.getString(2);
                    Long credId = null;
                    try {
                        long tmp = rs.getLong(3);
                        if (!rs.wasNull()) credId = tmp;
                    } catch (Exception ignore) {}
                    result.add(new ClientRecord(id, name, credId));
                }
            }
        }
        return result;
    }
}
