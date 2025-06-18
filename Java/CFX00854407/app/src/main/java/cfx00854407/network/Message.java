/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package cfx00854407.network;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 *
 * @author z003urxb
 */
public class Message implements AFFCARMessage {
	private static final Logger LOGGER = LogManager.getLogger(Message.class);

	public static final int MSG_SIZE = 8;

	public byte AFFCAR_1_Mode = (byte) 0xff;
	public byte AFFCAR_2_Mode = (byte) 0xff;
	private int Countdown_value = (byte) 0x00;
	public byte Display_Color = (byte) 0x00;
	public byte Clear = (byte) 0x00;

	public Message() {
	}

	public void setAffcarMode(boolean affcar1, boolean affcar2) {
		AFFCAR_1_Mode = 0x00;
		AFFCAR_2_Mode = 0x00;
		if (affcar1) {
			AFFCAR_1_Mode = 0x01;
		}
		if (affcar2) {
			AFFCAR_2_Mode = 0x01;
		}
	}

	public void setCountdownValue(int value) {
		Countdown_value = value;
	}

	public void setDisplayColor(boolean displayColor) {
		if (displayColor == cfx00854407.constants.Constants.DISPLAY_COLOR_BLOCKED) {
			Display_Color = 0x01;
		} else {
			Display_Color = 0x00;
		}
	}

	public void setClear(byte clear) {
		this.Clear = clear;
	}

	@Override
	public byte[] getBytes() throws PacketFormatException {
		byte[] packetData = new byte[8];

		packetData[0] = AFFCAR_1_Mode;
		packetData[1] = AFFCAR_2_Mode;
		packetData[2] = (byte) ((Countdown_value >> 24) & 0xff);
		packetData[3] = (byte) ((Countdown_value >> 16) & 0xff);
		packetData[4] = (byte) ((Countdown_value >> 8) & 0xff);
		packetData[5] = (byte) (Countdown_value & 0xff);

		LOGGER.info(
				() -> "Countdown_value: " + Countdown_value + ", Display_Color:" + Display_Color + ", Clear:" + Clear);

		packetData[6] = Display_Color;
		packetData[7] = Clear;

//        if(AFFCAR_1_Mode > 0x01 || AFFCAR_2_Mode > 0x01){
//            throw new PacketFormatException("AFFCAR Mode not specified properly.");
//        }

		return packetData;
	}

	@Override
	public void putBytes(byte[] bytes) {
		throw new UnsupportedOperationException("Not supported yet."); // To change body of generated methods, choose
																		// Tools | Templates.
	}
}
