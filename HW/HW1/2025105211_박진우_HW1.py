import statistics

def get_grade_and_point(rank, total):
    """
    등수에 따른 4.3 만점 기준 학점 및 학점값을 반환합니다.
    일반적인 대학의 상대평가 비율을 따릅니다: A학점(최대 30%), B학점(최대 40%, 누적 70%), C학점 이하(30%)
    """
    ratio = rank / total
    
    # A 학점 (상위 ~30%)
    if ratio <= 0.10:
        return 'A+', 4.3
    elif ratio <= 0.20:
        return 'A0', 4.0
    elif ratio <= 0.30:
        return 'A-', 3.7
        
    # B 학점 (상위 30% ~ 70%)
    elif ratio <= 0.45:
        return 'B+', 3.3
    elif ratio <= 0.60:
        return 'B0', 3.0
    elif ratio <= 0.70:
        return 'B-', 2.7
        
    # C 학점 (상위 70% ~ 90%)
    elif ratio <= 0.80:
        return 'C+', 2.3
    elif ratio <= 0.90:
        return 'C0', 2.0
    elif ratio <= 0.95:
        return 'C-', 1.7
        
    # D 학점 및 F 학점
    elif ratio <= 0.97:
        return 'D+', 1.3
    elif ratio <= 0.99:
        return 'D0', 1.0
    else:
        return 'F', 0.0

def main():
    print("=== 대학 성적 산출 프로그램 (4.3 만점 기준) ===")
    
    # 정원 입력
    while True:
        try:
            total_students = int(input("수강 정원을 입력하세요 (예: 30): "))
            if total_students > 0:
                break
            else:
                print("수강 정원은 1명 이상이어야 합니다.")
        except ValueError:
            print("올바른 숫자(정수)를 입력해주세요.")
            
    # 성적 입력
    scores = []
    print(f"\n총 {total_students}명의 성적(0~100점)을 차례대로 입력해주세요.")
    for i in range(total_students):
        while True:
            try:
                score = float(input(f"학생 {i+1}의 성적: "))
                if 0 <= score <= 100:
                    scores.append(score)
                    break
                else:
                    print("성적은 0에서 100 사이의 값이어야 합니다.")
            except ValueError:
                print("올바른 숫자를 입력해주세요.")
                
    # 통계 계산
    average = sum(scores) / total_students
    median = statistics.median(scores)
    
    # 출력창
    print("\n" + "="*45)
    print(f"전체 평균 점수: {average:.2f}점")
    print(f"전체 중앙값:   {median:.2f}점")
    print("="*45)
    
    # 동점자 처리를 위해 성적만 내림차순으로 정렬한 리스트 생성
    sorted_scores = sorted(scores, reverse=True)
    
    print("\n[ 학생별 학점 산출 결과 ]")
    print(f"{'학생':<6} | {'점수':<6} | {'등수':<6} | {'학점':<4} | {'평점':<4}")
    print("-" * 45)
    
    for i, score in enumerate(scores):
        # list.index()는 리스트에서 해당 값이 처음 등장하는 위치를 반환하므로 동점자의 경우 같은 (높은) 등수를 받게 됨
        rank = sorted_scores.index(score) + 1
        grade, point = get_grade_and_point(rank, total_students)
        
        print(f"학생 {i+1:<4} | {score:>5.1f}점 | {rank:>3}/{total_students} | {grade:<4} | {point:>4.1f}")

if __name__ == "__main__":
    main()
