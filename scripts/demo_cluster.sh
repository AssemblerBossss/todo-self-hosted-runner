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
