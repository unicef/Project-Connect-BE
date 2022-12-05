-- clean managed tables
drop table if exists public.dailycheckapp_measurements;

-- create tables & relations
CREATE TABLE public.dailycheckapp_measurements (
    id serial,
    "Timestamp" timestamp with time zone,
    "UUID" text,
    "BrowserID" text,
    school_id text NOT NULL,
    "DeviceType" text,
    "Notes" text,
    "ClientInfo" jsonb,
    "ServerInfo" jsonb,
    annotation text,
    "Download" double precision,
    "Upload" double precision,
    "Latency" bigint,
    "Results" jsonb
);
