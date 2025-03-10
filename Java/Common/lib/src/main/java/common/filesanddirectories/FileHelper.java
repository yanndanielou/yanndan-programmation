package common.filesanddirectories;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class FileHelper {
	private static final Logger LOGGER = LogManager.getLogger(FileHelper.class);

	public static List<File> getFileFromFullPaths(List<String> filesFullPaths) {
		List<File> files = new ArrayList<File>();
		filesFullPaths.forEach(e -> {
			File file = new File(e);
			files.add(file);
		});
		return files;
	}

	public static boolean removeFileIfExists(String fileName) {
		File myObj = new File(fileName);
		if (myObj.delete()) {
			LOGGER.info(() -> "Delete previous version of file file:" + fileName);
			return true;
		} else {
			LOGGER.info(() -> "File :" + fileName + " not deleted: probably not present");
			return false;
		}
	}

}
