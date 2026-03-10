[33mcommit 4d0f9bbfd6c8bfc187e45652f1e944b5838b3fdb[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmaster[m[33m, [m[1;31morigin/master[m[33m)[m
Merge: 27e0978 df67f4c
Author: AssemblerBossss <144702316+AssemblerBossss@users.noreply.github.com>
Date:   Thu Mar 5 20:35:02 2026 +0300

    Merge pull request #8 from DimoonNazarov/Todoauthentication
    
    Todoauthentication

[1mdiff --cc app/main.py[m
[1mindex 609d69a,27a0f5a..7167bd5[m
[1m--- a/app/main.py[m
[1m+++ b/app/main.py[m
[36m@@@ -7,10 -7,16 +7,17 @@@[m [mfrom fastapi.staticfiles import StaticF[m
  from fastapi.responses import RedirectResponse[m
  [m
  from app.core.database import get_es_client[m
[32m+ from app.exceptions import NotFoundException, InvalidPageException[m
  from app.repository.elastic_repository import ElasticRepository[m
[31m- from app.routers import todo_router, elastic_router, auth_router[m
[32m+ from app.routers import ([m
[32m+     todo_router,[m
[32m+     elastic_router,[m
[32m+     auth_router,[m
[32m+     not_found_handler,[m
[32m+     invalid_page_handler,[m
[32m+ )[m
  from app.utils import create_dirs[m
[32m +from app.middleware import JwtAuthMiddleware[m
  [m
  [m
  @asynccontextmanager[m
