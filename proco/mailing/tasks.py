from proco.taskapp import app


@app.task(ignore_result=True)
def send_email(backend, *args, **kwargs):
    backend.send(*args, **kwargs)
