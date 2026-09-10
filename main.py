import ui

def main():
    while True:
        try:
            ui.new_last_percent()
            ui.clear()
            ui.start()
        except KeyboardInterrupt:
            ui.clear()
            # التعامل مع إغلاق البرنامج بواسطة Ctrl+C
            print("\nExiting program...")
            break
        except Exception as e:
            # إظهار الخطأ لمعرفته أثناء التطوير بدلاً من تجاهله
            print(f"An unexpected error occurred: {e}")
            break
    
if __name__ == "__main__":
    main()