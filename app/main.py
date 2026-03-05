from core.realtime_monitor import main
from storage.database import init_database

if __name__ == "__main__":
    init_database()
    main()
