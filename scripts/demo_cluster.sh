#!/bin/bash
# Скрипт демонстрации кластера Elasticsearch

ES="http://localhost:9200"
ES2="http://localhost:9201"
ES3="http://localhost:9202"
INDEX="demo"

echo "========================================"
echo " 1. Состав кластера и текущий мастер"
echo "========================================"
echo "--- Узлы кластера ---"
curl -s "$ES/_cat/nodes?v&h=ip,name,master,role,heap.percent,ram.percent"
echo ""
echo "--- Текущий мастер-узел ---"
curl -s "$ES/_cat/master?v"
echo ""

echo "========================================"
echo " 2. Создать индекс: 3 шарда, 1 реплика"
echo "========================================"
curl -s -X DELETE "$ES/$INDEX" > /dev/null 2>&1
curl -s -X PUT "$ES/$INDEX" -H 'Content-Type: application/json' -d '{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  }
}' | python3 -m json.tool
echo ""
