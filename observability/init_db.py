from observability.database import Base,engine
from observability import observability_models

def initialize_database():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    initialize_database()
    print("Observability database initialized successfully.")


    