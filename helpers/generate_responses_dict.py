from typing import List
import models.responses

STATUS_CODE_RESPONSE_MAP = {
     # need to change response model when it's properly coding
    400: {'desc': models.responses.STATUS400_DESC, 'model': models.responses.HTTPExceptionRes},
    401: {'desc': models.responses.STATUS401_DESC, 'model': models.responses.HTTPExceptionRes},
    403: {'desc': models.responses.STATUS403_DESC, 'model': models.responses.HTTPExceptionRes},
    404: {'desc': models.responses.STATUS404_DESC, 'model': models.responses.HTTPExceptionRes},
    413: {'desc': models.responses.STATUS413_DESC, 'model': models.responses.HTTPExceptionRes},
    415: {'desc': models.responses.STATUS415_DESC, 'model': models.responses.HTTPExceptionRes},
    500: {'desc': models.responses.STATUS500_DESC, 'model': models.responses.HTTPExceptionRes},
}

def gen_res_dict(
    status_codes: List[int] = None,
    # custom_responses: dict = None
    ) -> dict:
    generated = {}
    if status_codes != None:
        for code in status_codes:
            desc_model = {
                'description': STATUS_CODE_RESPONSE_MAP[code]['desc'],
                'model': STATUS_CODE_RESPONSE_MAP[code]['model']
            }
            generated[code] = desc_model
    return generated
