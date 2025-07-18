services:
  - type: worker
    name: monitor-php-loop-python
    runtime: python
    region: frankfurt
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python3 servidor_render.py
    autoDeploy: true
