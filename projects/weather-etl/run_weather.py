from src.pipeline import(
    create_s3_client,
    run_weather_pipeline,
    url,
    params
)

def main():

    try:
        # 1. Create MinIO client
        s3_client = create_s3_client()

        # 2. Execute weather pipeline
        result= run_weather_pipeline(url, params, s3_client,)

        # 3. Display results
        print("Weather ETL completed successfully!")
        print(result)

    except Exception as e :
        print(f"pipeline failed {e}")
        raise


if __name__ == "__main__":
    main()
