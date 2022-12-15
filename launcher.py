import fire
import uvicorn


class Launcher:
    def web(self):
        uvicorn.run(
            'simaple.app.interface.web:app',
            host="0.0.0.0",
            log_level="trace",
            reload=True,
        )


if __name__ == "__main__":
    fire.Fire(Launcher)
