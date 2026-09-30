import json
import pytest
from scripts.acceptance_review import review_campaign


def test_provider_failure_cannot_be_scored_as_semantic_miss(tmp_path):
    (tmp_path/'plan.json').write_text(json.dumps({'cases':[{'id':'case','target':{'expected':'CONFIRMED'}}], 'jobs':[{}]}))
    record = {'job_index':0,'case':'case','arm':'on','summary':{'audit_id':'a','status':'INCOMPLETE','failure':'RuntimeError: Model HTTP error 402','snapshot_sha256':'abc'}}
    (tmp_path/'results.jsonl').write_text(json.dumps(record)+'\n')
    assert review_campaign(tmp_path)['reviewed_runs'] == 0
    review = [{'job_index':0,'target_outcome':'FN','additional_false_positives':0,'reviewer':'test reviewer','rationale_with_references':'provider failure'}]
    path = tmp_path/'reviews.json'; path.write_text(json.dumps(review))
    with pytest.raises(ValueError, match='Provider-refused'):
        review_campaign(tmp_path, path)
    review[0]['target_outcome'] = 'UNRESOLVED'; path.write_text(json.dumps(review))
    result = review_campaign(tmp_path, path)
    assert result['groups']['case/on']['UNRESOLVED'] == 1
    assert not result['all_runs_complete']
