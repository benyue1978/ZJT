"""
Video generation task processing
"""
import logging
from datetime import datetime, timedelta
from model import TasksModel, AIToolsModel
from config.constant import TASK_TYPE_GENERATE_VIDEO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_next_retry_delay(try_count):
    """
    Calculate next retry delay time
    
    Args:
        try_count: Number of attempts made
    
    Returns:
        Delay in seconds, maximum 360 seconds
    """
    base_delay = 3
    max_delay = 360
    delay_seconds = base_delay * (2 ** (try_count - 1))
    return min(delay_seconds, max_delay)


def process_generate_video(task):
    """Process video generation task logic"""
    try:
        logger.info(f"Processing video generation task: {task.task_id}")
        ai_tool = AIToolsModel.get_by_id(task.task_id)
        if not ai_tool:
            logger.error(f"Failed to get AI tool record by ID {task.task_id}")
            return False, -1
        if ai_tool.status == 0:
            logger.info(f"AI tool {task.task_id} is not ready")
            return False, 0
        elif ai_tool.status == 1:
            logger.info()
        return True
        
    except Exception as e:
        logger.error(f"Failed to process video generation task: {str(e)}")
        return False, -1


def process_task_with_retry(task_type, process_func):
    """
    Generic task processing function with retry logic
    
    Args:
        task_type: Task type
        process_func: Specific task processing function
    
    Returns:
        Tuple of (has_task, process_result)
    """
    try:
        # Query tasks by type with status 0 (队列中) or 1 (处理中)
        tasks = TasksModel.list_by_type_and_status(task_type, status_list=[0, 1])
        
        if not tasks:
            logger.info(f"No pending {task_type} tasks with status 0 or 1")
            return False, False
        
        logger.info(f"Found {len(tasks)} tasks to process for type: {task_type}")
        
        # Loop through all tasks
        processed_count = 0
        success_count = 0
        
        for task in tasks:
            try:
                logger.info(f"Start processing task: {task.task_id}, status: {task.status}")
                
                # Update status to 1 (处理中) if it's 0 (队列中)
                if task.status == 0:
                    TasksModel.update_by_task_id(task.task_id, status=1)
                    logger.info(f"Updated task {task.task_id} status to 1 (处理中)")
                
                # Call the specific processing function
                success,status = process_func(task)
                processed_count += 1
                
                if success:
                    # Success - update status to 2 (处理完成)
                    TasksModel.update_by_task_id(task.task_id, status=status)
                    logger.info(f"Task completed successfully: {task.task_id}, status updated to 2 (处理完成)")
                    success_count += 1
                else:
                    # Failed - increment retry count and update status to -1 (处理失败)
                    new_try_count = (task.try_count or 0) + 1
                    delay_seconds = calculate_next_retry_delay(new_try_count)
                    next_trigger = datetime.now() + timedelta(seconds=delay_seconds)
                    
                    TasksModel.update_by_task_id(
                        task.task_id,
                        try_count=new_try_count,
                        next_trigger=next_trigger
                    )
                    logger.info(f"Task failed: {task.task_id}, retry count: {new_try_count}, status: -1 (处理失败), next trigger: {next_trigger}")
                    
            except Exception as e:
                logger.error(f"Error processing task {task.task_id}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                
        logger.info(f"Processed {processed_count} tasks, {success_count} succeeded")
        return processed_count > 0, success_count > 0
            
    except Exception as e:
        logger.error(f"Task processing error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False, False


def generate_video_task(app=None):
    """Video generation task entry point"""
    process_task_with_retry(TASK_TYPE_GENERATE_VIDEO, process_generate_video)
