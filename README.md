# DRILL11 — AutoRun 상태 추가

2D 게임 프로그래밍 실습: `Idle`, `Run`, `AutoRun`을 별도 클래스로 구현했다.
강의 저장소 `unreal-class/2026-2DGP`의 캐릭터 실습 코드와 이미지를 바탕으로 한다.

## 실행

Python과 `pico2d`, `transitions`가 필요하다. 이 폴더에서 실행한다.

```shell
python -m pip install pico2d transitions
python main.py
```

이미지는 소스 파일 위치를 기준으로 읽으므로 다른 폴더에서도 `main.py`의 경로를 지정해 실행할 수 있다.

## 조작

| 입력 | 동작 |
| --- | --- |
| 왼쪽 / 오른쪽 방향키 | 일반 Run으로 이동. 키를 놓으면 Idle로 복귀 |
| Idle에서 A | 바라보는 방향으로 AutoRun 시작 |
| AutoRun에서 왼쪽 / 오른쪽 방향키 | AutoRun을 취소하고 누른 방향으로 일반 Run |
| ESC | 종료 |

- 일반 달리기: 초당 200픽셀, 100×100 크기.
- 자동 달리기: 초당 400픽셀, 150×150 크기. 입력 없이 계속 이동한다.
- 확대된 이미지가 화면을 벗어나지 않도록 좌우 끝에서 방향을 바꾼다.
- AutoRun 시작 후 5초가 지나면 Idle로 돌아오고 크기도 원래대로 복구된다.
- AutoRun 중 A를 다시 눌러도 5초 제한은 연장되지 않는다.
- 방향키를 함께 누르면 마지막에 누른 방향이 우선하며, 그 키를 놓으면 남은 키의 방향을 따른다.

## 구조

- `main.py`: 이벤트 전달, `get_time()`으로 프레임 간 경과 시간 계산, 화면 갱신.
- `boy.py`: `transitions.Machine`으로 상태 전환을 관리하고 각 상태 클래스에 갱신과 그리기를 위임.
- `grass.py`: 배경 잔디.
- `test_boy.py`: 화면을 열거나 실제로 5초를 기다리지 않고 동작을 검증하는 테스트.

`frame_time = current_time - previous_time`을 이동 거리와 제한 시간에 사용한다.
한 프레임이 오래 걸려도 여러 차례 벽에 반사된 위치를 계산하며, 5초 이후의 이동 시간은 반영하지 않는다.

## 검증

```shell
python -m unittest discover -s . -p test_boy.py -v
```

14개 테스트가 일반 이동, 자동 이동의 속도·크기, 양쪽 경계 반사, 5초 복귀,
재시작, 방향키 취소, 동시 입력과 이벤트 전달을 검증한다.
