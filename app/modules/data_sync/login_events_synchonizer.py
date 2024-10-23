from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
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
                user.RoleId,
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
            event_name: EventType = EventType.UserLoginWithOtp if session['RoleId'] == 2 else EventType.UserLoginWithPassword
            event_subject = EventSubject.LoginSession.value
            event_category = EventCategory.LoginSession.value
            event = {
                'UserId': session['UserId'],
                'TenantId': session['TenantId'],
                'SessionId': session['id'],
                'ResourceId': session['id'],
                'ResourceType': "User-Login-Session",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
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
                event_type: EventType = EventType.UserLoginWithOtp if session['RoleId'] == 2 else EventType.UserLoginWithPassword
                existing_event = DataSynchronizer.get_existing_event(session['UserId'], session['id'], event_type)
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

    @staticmethod
    def get_reancare_generate_otp_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND otp.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                otp.id, 
                otp.UserId,
                otp.Purpose,
                otp.ValidFrom,
                otp.ValidTill,
                otp.CreatedAt,
                otp.UpdatedAt,
                otp.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            FROM otp as otp
            JOIN users user ON user.id = otp.UserId
            WHERE
                user.IsTestUser = 0
                AND
                otp.Purpose = 'Login'
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            print(rows)
            return rows
        except Exception as error:
            print("Error retrieving User Medication Delete Events:", error)
            return None
        
    @staticmethod
    def add_analytics_otp_generate_event(otp):
        try:
            event_name = EventType.UserGenerateOtp.value
            event_category = EventCategory.LoginSession.value
            event_subject = EventSubject.LoginSession.value

            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'Purpose': otp['Purpose'],
                'ValidFrom': otp['ValidFrom'],
                'ValidTill': otp['ValidTill'],
            }
            otp = {
                'UserId': otp['UserId'],
                'TenantId': otp['TenantId'],
                'SessionId': None,
                'ResourceId': otp['id'],
                'ResourceType': "User-Login-Session",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "Otp generated.",
                'Attributes': str(attributes),
                'Timestamp': otp['ValidFrom'],
                'UserRegistrationDate': otp['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(otp)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
               return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_generate_otp_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            otps = LoginEventsSynchronizer.get_reancare_generate_otp_events(filters)
            if otps:
                for otp in otps:
                    existing_event = DataSynchronizer.get_existing_event(
                        otp['UserId'], otp['id'], EventType.UserGenerateOtp)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = LoginEventsSynchronizer.add_analytics_otp_generate_event(otp)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(otp)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Generate Otp Events found.")
        except Exception as error:
            print(f"Error syncing User Generate Otp Events: {error}")

    @staticmethod
    def get_reancare_user_logout_sessions(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND userDeviceDetail.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                userDeviceDetail.id,
                userDeviceDetail.UserId,
                userDeviceDetail.DeviceName,
                userDeviceDetail.OSType,
                userDeviceDetail.OSVersion,
                userDeviceDetail.AppName,
                userDeviceDetail.AppVersion,
                userDeviceDetail.ChangeCount,
                userDeviceDetail.CreatedAt,
                userDeviceDetail.UpdatedAt,
                userDeviceDetail.DeletedAt,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            FROM user_device_details userDeviceDetail
            JOIN users user ON user.id = userDeviceDetail.UserId
            WHERE
                user.IsTestUser = 0
                AND
                userDeviceDetail.DeletedAt IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Logout Sessions:", error)
            return None

    @staticmethod
    def add_logout_session_events(session):
        try:
            event_name: EventType = EventType.UserLogout
            event_subject = EventSubject.LoginSession.value
            event_category = EventCategory.LoginSession.value
            event = {
                'UserId': session['UserId'],
                'TenantId': session['TenantId'],
                'SessionId': session['id'],
                'ResourceId': session['id'],
                'ResourceType': "User-Login-Session",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User logged out.",
                'Attributes': "{}",
                'Timestamp': session['DeletedAt'],
                'UserRegistrationDate': session['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(event)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_user_logout_events(filters: DataSyncSearchFilter):
        
        try:
            existing_session_count = 0
            synched_session_count = 0
            session_not_synched = []
            sessions = LoginEventsSynchronizer.get_reancare_user_logout_sessions(filters)
            if sessions is None:
                print("No user login sessions found.")
                return None
            for session in sessions:
                existing_event = DataSynchronizer.get_existing_event(session['UserId'], session['id'], EventType.UserLogout)
                if existing_event is not None:
                    existing_session_count += 1
                    continue
                user = DataSynchronizer.get_user(session['UserId'])
                if user is not None:
                    LoginEventsSynchronizer.add_logout_session_events(session)
                    synched_session_count += 1
                else:
                    session_not_synched.append(session['id'])
                    print(f"User logout session {session['id']} not synced.")

            print(f"Total user logout sessions: {len(sessions)}")
            print(f"Existing user logout sessions: {existing_session_count}")
            print(f"Synched user logout sessions: {synched_session_count}")
            print(f"User logout sessions not synched: {len(session_not_synched)}")
            return session_not_synched
        except Exception as error:
            print("Error syncing user logout sessions:", error)
            return None
        


