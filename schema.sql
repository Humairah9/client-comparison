PRAGMA foreign_keys = ON;

CREATE TABLE author (
    author_id   INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE
);

CREATE TABLE book (
    book_id          INTEGER PRIMARY KEY,
    isbn             TEXT UNIQUE,                       -- optional: old or local books may have none
    title            TEXT NOT NULL,
    publication_year INTEGER CHECK (publication_year BETWEEN 1400 AND 2100)
);

CREATE TABLE book_author (
    book_id    INTEGER NOT NULL REFERENCES book(book_id)     ON DELETE CASCADE,
    author_id  INTEGER NOT NULL REFERENCES author(author_id) ON DELETE RESTRICT,
    PRIMARY KEY (book_id, author_id)
);

CREATE TABLE copy (
    copy_id      INTEGER PRIMARY KEY,
    book_id      INTEGER NOT NULL REFERENCES book(book_id) ON DELETE RESTRICT,
    barcode      TEXT NOT NULL UNIQUE,
    acquired_on  TEXT NOT NULL,                         -- ISO date, YYYY-MM-DD
    status       TEXT NOT NULL DEFAULT 'in_circulation'
                 CHECK (status IN ('in_circulation', 'lost', 'withdrawn'))
);

CREATE TABLE member (
    member_id  INTEGER PRIMARY KEY,
    full_name  TEXT NOT NULL,
    email      TEXT UNIQUE,                             -- NULL allowed (cleared when a member leaves)
    joined_on  TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'active'
               CHECK (status IN ('active', 'suspended', 'left')),
    left_on    TEXT,
    CHECK ((status = 'left') = (left_on IS NOT NULL))   -- left_on is set exactly when status is 'left'
);

CREATE TABLE loan (
    loan_id       INTEGER PRIMARY KEY,
    copy_id       INTEGER NOT NULL REFERENCES copy(copy_id)     ON DELETE RESTRICT,
    member_id     INTEGER NOT NULL REFERENCES member(member_id) ON DELETE RESTRICT,
    loaned_on     TEXT NOT NULL,
    due_on        TEXT NOT NULL,
    closed_on     TEXT,                                 -- NULL while the loan is open
    close_reason  TEXT CHECK (close_reason IN ('returned', 'lost')),
    CHECK (due_on >= loaned_on),
    CHECK (closed_on IS NULL OR closed_on >= loaned_on),
    CHECK ((closed_on IS NULL) = (close_reason IS NULL))
);
-- A physical copy can be out on at most one open loan at a time.
CREATE UNIQUE INDEX one_open_loan_per_copy ON loan(copy_id) WHERE closed_on IS NULL;
CREATE INDEX loan_by_member ON loan(member_id);

CREATE TABLE reservation (
    reservation_id  INTEGER PRIMARY KEY,
    book_id         INTEGER NOT NULL REFERENCES book(book_id)     ON DELETE RESTRICT,
    member_id       INTEGER NOT NULL REFERENCES member(member_id) ON DELETE RESTRICT,
    reserved_on     TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'waiting'
                    CHECK (status IN ('waiting', 'ready', 'fulfilled', 'cancelled', 'expired'))
);
-- A member can have only one live reservation per title.
CREATE UNIQUE INDEX one_live_reservation_per_member_title
    ON reservation(book_id, member_id) WHERE status IN ('waiting', 'ready');
