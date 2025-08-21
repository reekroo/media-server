from .oled_controller import OledController, log

def main():
    try:
        controller = OledController()
        controller.run()
    except KeyboardInterrupt:
        log.info("[OledController] stopped by user.")
    except Exception as e:
        log.critical(f"[OledController] failed to start: {e}", exc_info=True)

if __name__ == '__main__':
    main()