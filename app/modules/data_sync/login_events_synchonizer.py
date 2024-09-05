from app.domain_types.enums.event_types import EventType
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class LoginEventsSynchronizer:

    @staticmethod
    def get_reancare_user_login_sessions():
        try:
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                session.id,
                session.UserId,
                session.StartedAt,
                session.ValidTill,
                session.CreatedAt,
                user.id as UserId,
                user.TenantId,
                user.CreatedAt as UserRegistrationDate
            from user_login_sessions as session
            JOIN users as user ON session.UserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                session.DeletedAt IS NULL
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except mysql.connector.Error as error:
            print("Error retrieving User Login Sessions:", error)
            return None
        except Exception as error:
            print("Error retrieving User Login Sessions:", error)
            return None

    @staticmethod
    def add_login_session_events(session):
        try:
            event_name = EventType.UserLogin.value
            event = {
                'UserId': session['UserId'],
                'TenantId': session['TenantId'],
                'SessionId': session['id'],
                'ResourceId': session['id'],
                'ResourceType': "User-Login-Session",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "User-Login-Session",
                'ActionType': "User-Action",
                'ActionStatement': "User logged in.",
                'Attributes': "{}",
                'Timestamp': session['StartedAt'],
                'UserRegistrationDate': session['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(event)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                # print(f"Inserted row into the user_login_sessions table.")
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_user_login_events():
        try:
            existing_session_count = 0
            synched_session_count = 0
            session_not_synched = []
            sessions = LoginEventsSynchronizer.get_reancare_user_login_sessions()
            if sessions is None:
                print("No user login sessions found.")
                return None
            for session in sessions:
                existing_event = DataSynchronizer.get_existing_event(session['UserId'], session['id'], EventType.UserLogin)
                if existing_event is not None:
                    existing_session_count += 1
                    continue
                user = DataSynchronizer.get_user(session['UserId'])
                if user is not None:
                    LoginEventsSynchronizer.add_login_session_events(session)
                    synched_session_count += 1
                else:
                    session_not_synched.append(session['id'])
                    print(f"User login session {session['id']} not synced.")

            print(f"Total user login sessions: {len(sessions)}")
            print(f"Existing user login sessions: {existing_session_count}")
            print(f"Synched user login sessions: {synched_session_count}")
            print(f"User login sessions not synched: {len(session_not_synched)}")
            return session_not_synched
        except Exception as error:
            print("Error syncing user login sessions:", error)
            return None

############################################################

