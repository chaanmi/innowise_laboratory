# Основной список для хранения данных студентов
students = []

# Главный цикл программы с меню
while True:
    print("Student Grade Analyzer")
    print("1. Add a new student")
    print("2. Add a grades for a student")
    print("3. Show report(all students)")
    print("4. Find top performer")
    print("5. Exit")
    choice = input("Enter your choice: ")

    # Добавление нового студента
    if choice == "1":
        new_name = input("Enter student name:")
        exists = any(s["name"] == new_name for s in students)
        if exists:
            print("This student is alredy exists")
        else:
            new_dict = {"name": new_name, "grades": []}
            students.append(new_dict)

    # Добавление оценок для существующего студента
    elif choice == "2":
        name = input("Enter student name: ")
        exists_student = any(s["name"] == name for s in students)

        if exists_student:
            # Ищем конкретного студента чтобы добавить ему оценки
            for student in students:
                if student["name"] == name:
                    # Цикл для ввода нескольких оценок
                    while True:
                        grade_input = input("Enter a grade (or 'done' to finish): ")
                        if grade_input.lower() == "done":
                            break
                        try:
                            grade = float(grade_input)
                            if 0 <= grade <= 100:
                                student["grades"].append(grade)
                            else:
                                print("Grade must be between 0 and 100")
                        except ValueError:
                            print("Invalid input. Please enter a number.")
                    break
        else:
            print("There is no such student")

    # Показать отчет по всем студентам
    elif choice == "3":
        print("Student report")

        if not students:
            print("No students added")
            continue

        # Список для хранения средних баллов студентов с оценками
        averages = []
        for student in students:
            name = student.get("name", "")
            grades = student.get("grades", [])

            # Студенты без оценок
            if not grades:
                print(f"{name}'s average grade is N/A")
                continue

            # Расчет среднего балла
            try:
                average = sum(grades) / len(grades)
                print(f"{name}'s average grade is {average:.1f}")
                averages.append(average)
            except ZeroDivisionError:
                print(f"{name}'s average grade is N/A")

        # Вывод общей статистики если есть студенты с оценками
        if averages:
            print(f"Max Average: {max(averages):.1f}")
            print(f"Min Average: {min(averages):.1f}")
            print(f"Overall Average: {sum(averages)/len(averages):.1f}")

    # Поиск студента с наивысшим средним баллом
    elif choice == "4":
        if not students:
            print("No students added")
            continue

        # Фильтруем только студентов у которых есть оценки
        students_with_grades = [s for s in students if s["grades"]]

        if not students_with_grades:
            print("No students with grades")
            continue

        # Используем max с lambda функцией для поиска лучшего студента
        try:
            top_student = max(
                students_with_grades, key=lambda s: sum(s["grades"]) / len(s["grades"])
            )
            top_average = sum(top_student["grades"]) / len(top_student["grades"])
            print(
                f"The student with the highest average is {top_student['name']} with a grade of {top_average:.1f}"
            )
        except:
            print("Error finding top student")

    # Выход из программы
    elif choice == "5":
        print("Exiting program")
        break
