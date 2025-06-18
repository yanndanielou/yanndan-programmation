package cfx00854407.constants;

public interface Constants {

	public static final int PAE_CBTC_ADDRESS = 5121;
	public static final int AFFCAR_CBTC_ADDRESS = 1100;
	public static final String PAE_IP_ADDRESS = "172.40.0.62";
	public static final String AFFCAR_IP_ADDRESS = "172.40.0.41";
	public static final int PAE_AFFCAR_DESTINATION_PORT = 61440;
	public static final byte AFFCAR_PAE_MESSAGE_ID = 103;
	public static final byte PAE_AFFCAR_MESSAGE_ID = 102;
	public static final boolean ACK_REQUIRED = false;

	public static final boolean AFFCAR_1_MODE = true;
	public static final boolean AFFCAR_2_MODE = false;

	public static final boolean DISPLAY_COLOR_BLOCKED = true;
	public static final boolean DISPLAY_COLOR_NOT_BLOCKED = false;

	public static final int MESSAGES_FREQUENCY = 100;
	public static final int MESSAGES_PER_SECOND = 1000 / MESSAGES_FREQUENCY;

}
