import calendar
import matplotlib.pyplot as plt

from sqlalchemy.orm import Session
from sqlalchemy import func

from src.imports.jsonimport import import_watch_history_json
from src.db.objects import Channel, WatchHistory
from src.db.create import get_database_engine

# set up database
db_engine = get_database_engine()

# import watch history
# import_watch_history_json("input/watch-history.json", db_engine)

with Session(db_engine) as session:

    for year in range(2023, 2020, -1):

        months = ()
        counts = ()

        for month in range(1, 13):

            query = (
                session.query(func.count())
                .filter(func.extract('year', WatchHistory.timestamp) == year)
                .filter(func.extract('month', WatchHistory.timestamp) == month)
            )
            watch_count = query.scalar()

            print(f"{year}-{month}: {watch_count}")

            months += (calendar.month_abbr[month],)
            counts += (watch_count,)

        plt.plot(months, counts, label=f"{year}")
    
plt.xlabel('Month')
plt.xticks(rotation=90)
plt.ylabel('Count')
plt.title('Watches per month')

plt.legend()

plt.show()
