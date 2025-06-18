package cfx00854407.utils;

public class StringUtils {

	public static String transformBytesArrayToString(byte[] bytesArray) {

		StringBuilder hexString = new StringBuilder();
		for (byte b : bytesArray) {
			String hex = Integer.toHexString(0xff & b);
			if (hex.length() == 1) {
				hexString.append('0');
			}
			hexString.append(hex);
		}
		return hexString.toString();
	}

}
