from simaple.app.wasm import createUow, createSimulatorFromBaseline, runSimulatorWithPlan


def test_run_plan():
    uow = createUow()
    simulator_id = createSimulatorFromBaseline({
            "simulation_setting": {
                "tier": "Legendary",
                "jobtype": "archmagetc",
                "job_category": 1,
                "level": 280,
                "passive_skill_level": 0,
                "combat_orders_level": 1,
                "artifact_level": 40
            }
        }, uow)
    plan = '''
CAST "오버로드 마나"
CAST "이프리트"
CAST "메이플 용사"
CAST "메디테이션"
CAST "파이어 오라"
CAST "인피니티"
ELAPSE 78000

CAST "메이플월드 여신의 축복"

CAST "포이즌 리전" 
CAST "플레임 헤이즈 VI"

CAST "에픽 어드벤쳐"
CAST "소울 컨트랙트"
CAST "리스트레인트 링"
CAST "메기도 플레임"
CAST "인페르날 베놈"
CAST "퓨리 오브 이프리트"
CAST "포이즌 노바"
CAST "도트 퍼니셔"
CAST "포이즌 체인"
CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
CAST "크레스트 오브 더 솔라" 
CAST "플레임 스윕 VI"
CAST "플레임 스윕 VI"

CAST "메테오"

CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"

CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"

CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"

CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"

CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"    
'''
    response = runSimulatorWithPlan(simulator_id, plan, uow)
    response = runSimulatorWithPlan(simulator_id, plan, uow)
