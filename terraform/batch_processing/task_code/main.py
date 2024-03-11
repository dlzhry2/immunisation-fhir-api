import os

if __name__ == '__main__':
    print("hello from batch")
    print(f"bucket: {os.getenv('BUCKET_NAME')} key: {os.getenv('OBJECT_KEY')}")
