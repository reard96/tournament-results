#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


class DB:

    def __init__(self, db_con_str="dbname=tournament"):
        """
        Creates a database connection with the connection string provided
        :param str db_con_str: Contains the database connection string,
        with a default value when no argument is passed to the parameter
        """
        self.conn = psycopg2.connect(db_con_str)

    def cursor(self):
        """
        Returns the current cursor of the database
        """
        return self.conn.cursor()

    def execute(self, sql_query_string, and_close=False, values=None):
        """
        Executes SQL queries
        :param str sql_query_string: Contain the query string to be executed
        :param bool and_close: If true, closes the database connection after
        executing and commiting the SQL Query
        :param vales: Contain values to include in sql_query_string
        """
        cursor = self.cursor()
        cursor.execute(sql_query_string, values)
        if and_close:
            self.conn.commit()
            self.close()
        return {"conn": self.conn, "cursor": cursor if not and_close else None}

    def close(self):
        """
        Closes the current database connection
        """
        return self.conn.close()


def deleteMatches():
    """Remove all the match records from the database."""
    DB().execute("DELETE FROM matches", True)


def deletePlayers():
    """Remove all the player records from the database."""
    DB().execute("DELETE FROM players", True)


def countPlayers():
    """Returns the number of players currently registered."""
    conn = DB().execute("SELECT count(*) FROM players")
    cursor = conn["cursor"].fetchone()
    conn['conn'].close()
    return cursor[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB().execute("INSERT INTO players (name) VALUES (%s)", True, (name,))


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = DB().execute("SELECT id, name, wins, matches FROM Standings")
    playerRanks = conn["cursor"].fetchall()
    conn['conn'].close()
    return playerRanks


def reportMatch(winner, loser, tie=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    if tie:
        DB().execute("INSERT INTO matches (player1, player2, result) VALUES (%s, %s, 1)", True, (winner, loser))
        DB().execute("INSERT INTO matches (player1, player2, result) VALUES (%s, %s, 1)", True, (loser, winner))
    else:
        DB().execute("INSERT INTO matches (player1, player2, result) VALUES (%s, %s, 1)", True, (winner, loser))
        DB().execute("INSERT INTO matches (player1, player2, result) VALUES (%s, %s, 0)", True, (loser, winner))


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    results = playerStandings()
    return [(results[i-1][0], results[i-1][1], results[i][0], results[i][1])
            for i in range(1, len(results), 2)]
