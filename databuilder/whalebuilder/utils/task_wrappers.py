import os
import yaml

from whalebuilder.utils.paths import (  # noqa: F401
    BASE_DIR,
    CONNECTION_PATH,
    MANIFEST_PATH,
    TMP_MANIFEST_PATH
)
from whalebuilder.task import WhaleTask
from whalebuilder.loader.whale_loader import WhaleLoader
from whalebuilder.transformer.markdown_transformer import MarkdownTransformer
from whalebuilder.utils.connections import dump_connection_config_in_schema
from whalebuilder.utils import transfer_manifest

from whalebuilder.utils.extractor_wrappers import \
        configure_bigquery_extractors, \
        configure_neo4j_extractors, \
        configure_presto_extractors, \
        configure_snowflake_extractors, \
        run_build_script


def create_and_run_tasks_from_yaml(
        is_full_extraction_enabled=True,
        verbose=True):
    with open(CONNECTION_PATH) as f:
        raw_connection_dicts = list(yaml.safe_load_all(f))

    for raw_connection_dict in raw_connection_dicts:
        connection = dump_connection_config_in_schema(raw_connection_dict)

        if connection.metadata_source == 'presto':
            extractors, conf = configure_presto_extractors(
                    connection,
                    is_full_extraction_enabled=is_full_extraction_enabled)
        elif connection.metadata_source == 'neo4j':
            extractors, conf = configure_neo4j_extractors(connection)
        elif connection.metadata_source == 'bigquery':
            extractors, conf = configure_bigquery_extractors(connection)
        elif connection.metadata_source == 'snowflake':
            extractors, conf = configure_snowflake_extractors(connection)
        elif connection.metadata_source == 'build_script':
            run_build_script(connection)
            break
        else:
            break

        # If another ETL job is running, put the manifest elsewhere
        tmp_manifest_path = TMP_MANIFEST_PATH
        i = 0
        while os.path.exists(tmp_manifest_path):
            tmp_manifest_path = os.path.join(
                BASE_DIR,
                "manifests/tmp_manifest_" + str(i) + ".txt")
            i += 1
        manifest_key = 'loader.whale.tmp_manifest_path'
        conf.put('loader.whale.database_name', connection.name)
        conf.put(manifest_key, tmp_manifest_path)

        for i, extractor in enumerate(extractors):
            task = WhaleTask(
                extractor=extractor,
                transformer=MarkdownTransformer(),
                loader=WhaleLoader(),
            )
            task.init(conf)
            task.run()

            # The first extractor passes all tables, always
            # No need to update the manifest after the first time
            if i == 0:
                task.save_stats()
                conf.pop(manifest_key)
                transfer_manifest(tmp_manifest_path)

