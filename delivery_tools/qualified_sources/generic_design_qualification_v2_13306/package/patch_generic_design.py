"""Narrow generic pipeline validation; preserve Physical V3 scientific/control-flow code."""
ANCHOR_CONFIG = '    return data\n\ndef put(run,name,data):'
ANCHOR_DESIGN = '        put(run,"candidates",candidates);put(run,"config",config)'
ANCHOR_EVALUATE = '        reused=None'
POLICY = """    settings=data.get("design",{})
    for key,default in (("backbones",4),("sequences_per_backbone",4),("binder_length",65)):
        value=settings.get(key,default)
        require(type(value) is int and value>0,"INVALID_CONFIG",f"design.{key} must be a positive non-boolean integer")
    require(1<=settings.get("backbones",4)<=1000,"INVALID_DESIGN_COUNT","Backbones must be 1-1000")
    require(30<=settings.get("binder_length",65)<=200,"UNSUPPORTED_BINDER_LENGTH","Supported miniprotein length 30-200")
    temperature=settings.get("temperature",.1)
    valid_temperature=isinstance(temperature,(int,float)) and not isinstance(temperature,bool)
    if valid_temperature:
        try:valid_temperature=bool(np.isfinite(float(temperature))) and temperature>0
        except (OverflowError,ValueError,TypeError):valid_temperature=False
    require(valid_temperature,
            "INVALID_DESIGN_TEMPERATURE","design.temperature must be one finite positive numeric sampling temperature")
"""
POOL = """        require(isinstance(candidates,list),"INVALID_DESIGN_POOL","The generic design pool must be a list")
        require(bool(candidates),"EMPTY_DESIGN_POOL","The generic workflow cannot accept or evaluate an empty design pool")
"""
def patch(text):
    for anchor in (ANCHOR_CONFIG,ANCHOR_DESIGN,ANCHOR_EVALUATE):
        if text.count(anchor)!=1:raise ValueError("Exactly one unmodified generic pipeline anchor required: "+anchor)
    if '"EMPTY_DESIGN_POOL"' in text or '"INVALID_DESIGN_TEMPERATURE"' in text:
        raise ValueError("Generic design validation patch was already applied or collided")
    changed=text.replace(ANCHOR_CONFIG,POLICY+ANCHOR_CONFIG)
    changed=changed.replace(ANCHOR_DESIGN,POOL+ANCHOR_DESIGN)
    changed=changed.replace(ANCHOR_EVALUATE,POOL+ANCHOR_EVALUATE)
    return changed

