package com.mediant.api.dataexchange.trigger;

public final class SQLErrorCode {
    public static final int DUPLICATE_KEY = 2627; // SQL Server duplicate key
    public static final int CONSTRAINT_VIOLATION = 547;

    private SQLErrorCode() {}
}
